      program surf_xyt_dy
c
c Read daily files like sst_xyt_dy.ascii, uwnd_xyt_dy.ascii, ...
c   from the TAO/TRITON data delivery page
c
      implicit none
c
      integer nx, ny, nt
      parameter(nx = 29, ny = 17, nt = 20000)
      real var(nx,ny,nt), lon(nx), lat(ny), flag
      integer iqual(nx,ny,nt), isrc(nx,ny,nt), idate(nt)
c
      integer nlon, nlat, ntim
c
      integer i, j, n, iyr, imon, iday
c
      character*80 infile, header
      character*256 line, line2
c
      integer inosrc
c
c.......................................................................
c
      inosrc = 0
c
      write(*,*) ' Enter the input file name'
      read(*,'(a)') infile
c
      if(index(infile,'dyn')  .gt. 0 .or. 
     .   index(infile,'iso')  .gt. 0 .or.
     .   index(infile,'heat') .gt. 0) then
        inosrc = 1
      endif
c
      open(1,file=infile,status='old',form='formatted')
c
c Read the missing data flag
c
      read(1,'(a)') header
      read(1,20) flag
   20 format(86x,f11.3)
      write(*,*) flag
c
c Read in the number of longitues, latitudes, and times
c
      read(1,22) nlon, nlat, ntim
   22 format(7x,i3, 8x,i3, 8x,i6)
      write(*,*) nlon, nlat, ntim
c
c Read in lon, lat, and depth axes
c
      call blank(line)
      read(1,'(a)') line
      line2 = line(7:)
      read(line2,*) (lon(i), i=1,nlon)
c
      call blank(line)
      read(1,'(a)') line
      line2 = line(7:)
      read(line2,*) (lat(j), j=nlat,1,-1)
c
      write(*,*) (lon(i),  i=1,nlon)
      write(*,*) (lat(j),  j=nlat,1,-1)
c
c  Initialize ts array to flag and iqual array to 5.
c
      do i = 1, nx
        do j = 1, ny
          do n = 1, nt
              var(i,j,n) = flag
            iqual(i,j,n) = 5
             isrc(i,j,n) = 0
          enddo
        enddo
      enddo
c
      do n = 1, ntim
        read(1,50) iyr, imon, iday
        idate(n) = iyr*10000 + imon*100 + iday
        do j = nlat, 1, -1
          if(inosrc .eq. 1) then
            read(1,*) (var(i,j,n),iqual(i,j,n),i=1,nlon)
          else
            read(1,*) (var(i,j,n),iqual(i,j,n),isrc(i,j,n),i=1,nlon)
          endif
        enddo
      enddo
   50 format(6x,i4,1x,i2,1x,i2)
c
      do n = 1, ntim
        write(*,*) idate(n)
        do j = nlat, 1, -1
          if(inosrc .eq. 1) then
            write(*,*) (var(i,j,n),iqual(i,j,n),i=1,nlon)
          else
            write(*,*) (var(i,j,n),iqual(i,j,n),isrc(i,j,n),i=1,nlon)
          endif
        enddo
      enddo
c
      end
c
ccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
c
      subroutine blank(string)
c
c blank out the string from 1 to its declared length
c
      character*(*) string
c
      integer i
c
      do i = 1, len(string)
        string(i:i) = ' '
      enddo
c
      return
      end
